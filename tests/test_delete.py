import asyncio

import pytest

import boostedblob as bbb

from . import helpers


@pytest.mark.asyncio
@bbb.ensure_session
async def test_remove(any_dir):
    assert [p async for p in bbb.listdir(any_dir)] == []
    helpers.create_file(any_dir / "alpha")

    with pytest.raises((IsADirectoryError, PermissionError)):
        await bbb.remove(any_dir)

    assert [p.name async for p in bbb.listdir(any_dir)] == ["alpha"]
    await bbb.remove(any_dir / "alpha")
    assert [p async for p in bbb.listdir(any_dir)] == []


@pytest.mark.asyncio
@bbb.ensure_session
async def test_rmtree(any_dir):
    assert [p async for p in bbb.listdir(any_dir)] == []

    N = 5
    await asyncio.wait(
        [helpers.unsafe_create_file(any_dir / "alpha" / str(i)) for i in range(N)]
        + [helpers.unsafe_create_file(any_dir / "alpha" / "beta" / str(i)) for i in range(N)]
    )
    with pytest.raises(NotADirectoryError):
        async with bbb.BoostExecutor(N) as e:
            await bbb.rmtree(any_dir / "alpha" / "0", e)

    async with bbb.BoostExecutor(N) as e:
        assert len([p async for p in bbb.listdir(any_dir / "alpha")]) == N + 1
        assert len([p async for p in bbb.listtree(any_dir / "alpha")]) == 2 * N
        await bbb.rmtree(any_dir / "alpha", e)

    with pytest.raises(FileNotFoundError):
        async with bbb.BoostExecutor(N) as e:
            await bbb.rmtree(any_dir / "alpha", e)

    with pytest.raises(FileNotFoundError):
        [p async for p in bbb.listdir(any_dir / "alpha")]
    assert [p async for p in bbb.listdir(any_dir)] == []
    assert [p async for p in bbb.listtree(any_dir)] == []
